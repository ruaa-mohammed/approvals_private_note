from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.osv import expression


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    def _get_message_create_valid_field_names(self):
        return super()._get_message_create_valid_field_names() | {'is_private_note'}

    def message_post(self, **kwargs):
        if kwargs.get('is_private_note') and (kwargs.get('attachment_ids') or kwargs.get('attachments')):
            raise UserError(_("Private notes cannot have attachments."))
        if kwargs.get('is_private_note'):
            allowed_partner_ids = set(self.approver_ids.mapped('user_id.partner_id').ids)
            mentioned_partner_ids = set(kwargs.get('partner_ids') or [])
            if not mentioned_partner_ids <= allowed_partner_ids:
                raise UserError(_("Private notes can only be sent to employees assigned to approve this request."))
        return super().message_post(**kwargs)

    @api.model
    def get_private_note_mention_suggestions(self, request_id, search, limit=8):
        request = self.browse(request_id).exists()
        if not request:
            return []
        request.check_access_rights('read')
        request.check_access_rule('read')

        partners = self.env['res.partner']
        allowed_partner_ids = request.approver_ids.mapped('user_id.partner_id').ids
        if not allowed_partner_ids:
            return []
        domain = expression.AND([
            partners._get_mention_suggestions_domain(search),
            [('id', 'in', allowed_partner_ids)],
        ])
        suggested_partners = partners._search_mention_suggestions(domain, limit)
        return list(suggested_partners.mail_partner_format().values())

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        recipients = super()._notify_get_recipients(message, msg_vals, **kwargs)
        message_sudo = message.sudo()
        if message_sudo.is_private_note:
            # notify only the mentioned partners, never the followers, and in
            # Odoo (Inbox) only, never by email
            mentioned_ids = set(message_sudo.partner_ids.ids)
            recipients = [
                dict(recipient, notif='inbox')
                for recipient in recipients if recipient['id'] in mentioned_ids
            ]
        return recipients

    def _message_update_content(self, message, body, attachment_ids=None, **kwargs):
        if message.is_private_note and attachment_ids:
            raise UserError(_("Private notes cannot have attachments."))
        return super()._message_update_content(message, body, attachment_ids=attachment_ids, **kwargs)

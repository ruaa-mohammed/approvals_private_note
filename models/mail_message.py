import re
import textwrap

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression
from odoo.tools import html_to_inner_content


class MailMessage(models.Model):
    _inherit = 'mail.message'

    is_private_note = fields.Boolean('Private Note', readonly=True)
    approval_request_id = fields.Many2one(
        'approval.request',
        string='Approval',
        compute='_compute_approval_request_id',
        readonly=True,
        store=False,
    )
    can_delete_private_note = fields.Boolean(
        compute='_compute_can_delete_private_note',
    )

    @api.depends('model', 'res_id')
    def _compute_approval_request_id(self):
        for message in self:
            if message.model == 'approval.request' and message.res_id:
                message.approval_request_id = message.res_id
            else:
                message.approval_request_id = False

    @api.depends('is_private_note', 'author_id')
    @api.depends_context('uid')
    def _compute_can_delete_private_note(self):
        partner_id = self.env.user.partner_id.id
        for message in self:
            message.can_delete_private_note = (
                message.is_private_note and message.author_id.id == partner_id
            )

    def action_delete_private_note(self):
        if any(not message.is_private_note or message.model != 'approval.request' for message in self):
            raise UserError(_("Only private notes on approval requests can be deleted here."))
        self.unlink()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Private Notes'),
            'res_model': 'mail.message',
            'view_mode': 'tree',
            'views': [(self.env.ref(
                'approvals_private_note.mail_message_view_tree_private_note'
            ).id, 'tree')],
            'domain': [('model', '=', 'approval.request'), ('is_private_note', '=', True)],
        }

    def unlink(self):
        if not self.env.is_superuser():
            self.flush_recordset(['is_private_note', 'author_id'])
            partner_id = self.env.user.partner_id.id
            if any(
                message.is_private_note and message.author_id.id != partner_id
                for message in self
            ):
                raise AccessError(_("You can only delete private notes that you authored."))
        return super().unlink()

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        # private notes are only visible to their author and the mentioned partners
        if not self.env.is_superuser():
            partner_id = self.env.user.partner_id.id
            domain = expression.AND([domain, [
                '|', '|',
                ('is_private_note', '=', False),
                ('author_id', '=', partner_id),
                ('partner_ids', 'in', partner_id),
            ]])
        return super()._search(domain, offset, limit, order, access_rights_uid)

    def check_access_rule(self, operation):
        super().check_access_rule(operation)
        if self.env.is_superuser() or not self.ids:
            return
        self.flush_recordset(['is_private_note', 'author_id', 'partner_ids'])
        partner_id = self.env.user.partner_id.id
        self.env.cr.execute("""
            SELECT m.id
            FROM "mail_message" m
            WHERE m.id IN %s
                AND m.is_private_note IS TRUE
                AND m.author_id IS DISTINCT FROM %s
                AND NOT EXISTS (
                    SELECT 1
                    FROM "mail_message_res_partner_rel" partner_rel
                    WHERE partner_rel.mail_message_id = m.id
                        AND partner_rel.res_partner_id = %s
                )
        """, (tuple(self.ids), partner_id, partner_id))
        if self.env.cr.fetchall():
            raise AccessError(_("This private note is only visible to its author and the mentioned users."))

    def _get_message_preview(self, max_char=190):
        self.ensure_one()
        if not self.is_private_note:
            return super()._get_message_preview(max_char=max_char)

        body = self.body or ''
        body = re.sub(r'(?is)<a\b[^>]*class="[^"]*o_mention[^"]*"[^>]*>(.*?)</a>', r'\1', body)
        body = re.sub(r'(?is)<span\b[^>]*class="[^"]*o_mention[^"]*"[^>]*>(.*?)</span>', r'\1', body)
        body = re.sub(r'(?<!\w)@(?:[A-Za-z0-9_]+(?:\s+[A-Za-z0-9_]+)*)', ' ', body)
        preview = html_to_inner_content(body)
        preview = ' '.join(preview.split())
        return textwrap.shorten(preview, max_char) if max_char else preview

    def _get_message_format_fields(self):
        return super()._get_message_format_fields() + ['is_private_note']

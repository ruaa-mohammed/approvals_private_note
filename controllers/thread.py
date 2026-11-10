from odoo import http
from odoo.addons.mail.controllers.thread import ThreadController


class PrivateNoteThreadController(ThreadController):

    def _get_allowed_message_post_params(self):
        return super()._get_allowed_message_post_params() | {"is_private_note"}

    @http.route()
    def mail_message_post(self, thread_model, thread_id, post_data, context=None, **kwargs):
        # private notes only exist on approval requests
        if thread_model != "approval.request":
            post_data.pop("is_private_note", None)
        return super().mail_message_post(thread_model, thread_id, post_data, context=context, **kwargs)

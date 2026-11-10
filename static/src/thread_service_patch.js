/* @odoo-module */

import { ThreadService } from "@mail/core/common/thread_service";
import { patch } from "@web/core/utils/patch";

patch(ThreadService.prototype, {
    async getMessagePostParams({ thread }) {
        const params = await super.getMessagePostParams(...arguments);
        if (thread.composer?.isPrivateNote) {
            params.post_data.is_private_note = true;
        }
        return params;
    },
});

/* @odoo-module */

import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";

patch(Composer.prototype, {
    get allowUpload() {
        // private notes are text only, also when they are edited
        return super.allowUpload && !this.props.composer.message?.is_private_note;
    },

    async _sendMessage(value, postData) {
        // read by ThreadService.getMessagePostParams
        this.props.composer.isPrivateNote = this.env.chatterState?.composerType === "privateNote";
        return super._sendMessage(value, postData);
    },
});

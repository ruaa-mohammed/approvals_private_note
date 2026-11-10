/* @odoo-module */

import { Chatter } from "@mail/core/web/chatter";
import { useChildSubEnv } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        // lets the composer know which button opened it
        useChildSubEnv({ chatterState: this.state });
    },

    toggleComposer(mode = false) {
        super.toggleComposer(...arguments);
        if (this.state.thread?.composer) {
            this.state.thread.composer.isPrivateNote =
                this.state.composerType === "privateNote";
        }
    },

    changeThread(...args) {
        super.changeThread(...args);
        if (this.state.thread?.composer) {
            this.state.thread.composer.isPrivateNote =
                this.state.composerType === "privateNote";
        }
    },

    onClickSearch() {
        super.onClickSearch(...arguments);
        if (this.state.thread?.composer) {
            this.state.thread.composer.isPrivateNote = false;
        }
    },
});

/* @odoo-module */

import { SuggestionService } from "@mail/core/common/suggestion_service";
import { patch } from "@web/core/utils/patch";

patch(SuggestionService.prototype, {
    async fetchPartners(term, thread) {
        if (thread?.model === "approval.request" && thread.composer?.isPrivateNote) {
            const partners = await this.orm.silent.call(
                "approval.request",
                "get_private_note_mention_suggestions",
                [thread.id],
                { search: term }
            );
            this.store.Persona.insert(partners);
            this.privateNoteApproverPartnerIds ??= new Map();
            this.privateNoteApproverPartnerIds.set(
                thread.id,
                new Set(partners.map((partner) => partner.id))
            );
            return;
        }
        return super.fetchPartners(...arguments);
    },

    searchPartnerSuggestions(cleanedSearchTerm, thread, sort) {
        const suggestions = super.searchPartnerSuggestions(...arguments);
        if (thread?.model !== "approval.request" || !thread.composer?.isPrivateNote) {
            return suggestions;
        }
        const approverPartnerIds = this.privateNoteApproverPartnerIds?.get(thread.id);
        return {
            ...suggestions,
            mainSuggestions: suggestions.mainSuggestions.filter((partner) =>
                approverPartnerIds?.has(partner.id)
            ),
            extraSuggestions: suggestions.extraSuggestions.filter((partner) =>
                approverPartnerIds?.has(partner.id)
            ),
        };
    },
});

/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

/**
 * Custom Kanban Controller for Real Estate Properties
 */
class PropertyKanbanController extends KanbanController {
    /**
     * @override
     */
    setup() {
        super.setup();
    }

    /**
     * Quick create a new property
     *
     * @param {Object} data
     */
    async createProperty(data) {
        const context = this.props.context;
        await this.model.root.createRecord(context, data);
        this.render();
    }

    /**
     * Open a property in form view
     *
     * @param {Object} record
     */
    openPropertyForm(record) {
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'real.estate.property',
            res_id: record.resId,
            views: [[false, 'form']],
            target: 'current',
        });
    }
}

/**
 * Custom Kanban Renderer for Real Estate Properties
 */
class PropertyKanbanRenderer extends KanbanRenderer {
    /**
     * @override
     */
    setup() {
        super.setup();
    }
}

// Register the custom components as overrides
registry.category("views").add("property_kanban", {
    ...kanbanView,
    Controller: PropertyKanbanController,
    Renderer: PropertyKanbanRenderer,
});

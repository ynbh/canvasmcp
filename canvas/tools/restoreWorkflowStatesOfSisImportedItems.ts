
import { tool } from "ai";
import { restoreWorkflowStatesOfSisImportedItemsDataSchema } from "./aitm.schema.ts";
import { restoreWorkflowStatesOfSisImportedItems, RestoreWorkflowStatesOfSisImportedItemsData } from "..";

export default tool({
  description: `
  Restore workflow_states of SIS imported items
This will restore the the workflow_state for all the
items that changed
their workflow_state during the import being restored.
This will restore states
for items imported with the following importers:
accounts.csv terms.csv courses.csv sections.csv
group_categories.csv
groups.csv users.csv admins.csv
This also restores states for other items that
changed during the import.
An example would be if an enrollment was deleted from a sis import and
the
group_membership was also deleted as a result of the enrollment deletion,
both items would be
restored when the sis batch is restored.
    `,
  parameters: restoreWorkflowStatesOfSisImportedItemsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RestoreWorkflowStatesOfSisImportedItemsData, "url"> ) => {
    try {
      const { data } = await restoreWorkflowStatesOfSisImportedItems(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
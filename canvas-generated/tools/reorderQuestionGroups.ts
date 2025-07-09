
import { tool } from "ai";
import { reorderQuestionGroupsDataSchema } from "./aitm.schema.ts";
import { reorderQuestionGroups, ReorderQuestionGroupsData } from "..";

export default tool({
  description: `
  Reorder question groups
Change the order of the quiz questions within the group

<b>204 No
Content<b> response code is returned if the reorder was successful.
    `,
  parameters: reorderQuestionGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReorderQuestionGroupsData, "url"> ) => {
    try {
      const { data } = await reorderQuestionGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
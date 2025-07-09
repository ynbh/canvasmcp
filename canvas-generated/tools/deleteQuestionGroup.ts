
import { tool } from "ai";
import { deleteQuestionGroupDataSchema } from "./aitm.schema.ts";
import { deleteQuestionGroup, DeleteQuestionGroupData } from "..";

export default tool({
  description: `
  Delete a question group
Delete a question group

<b>204 No Content<b> response code is returned if
the deletion was successful.
    `,
  parameters: deleteQuestionGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteQuestionGroupData, "url"> ) => {
    try {
      const { data } = await deleteQuestionGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
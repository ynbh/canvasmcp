
import { tool } from "ai";
import { updateQuestionGroupDataSchema } from "./aitm.schema.ts";
import { updateQuestionGroup, UpdateQuestionGroupData } from "..";

export default tool({
  description: `
  Update a question group
Update a question group
    `,
  parameters: updateQuestionGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateQuestionGroupData, "url"> ) => {
    try {
      const { data } = await updateQuestionGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
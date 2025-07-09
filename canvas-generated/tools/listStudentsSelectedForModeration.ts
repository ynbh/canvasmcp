
import { tool } from "ai";
import { listStudentsSelectedForModerationDataSchema } from "./aitm.schema.ts";
import { listStudentsSelectedForModeration, ListStudentsSelectedForModerationData } from "..";

export default tool({
  description: `
  List students selected for moderation
Returns a paginated list of students selected for moderation
    `,
  parameters: listStudentsSelectedForModerationDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListStudentsSelectedForModerationData, "url"> ) => {
    try {
      const { data } = await listStudentsSelectedForModeration(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
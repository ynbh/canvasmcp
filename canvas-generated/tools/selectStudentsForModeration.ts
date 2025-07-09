
import { tool } from "ai";
import { selectStudentsForModerationDataSchema } from "./aitm.schema.ts";
import { selectStudentsForModeration, SelectStudentsForModerationData } from "..";

export default tool({
  description: `
  Select students for moderation
Returns an array of users that were selected for moderation
    `,
  parameters: selectStudentsForModerationDataSchema.omit({ url: true }),
  execute: async (args : Omit<SelectStudentsForModerationData, "url"> ) => {
    try {
      const { data } = await selectStudentsForModeration(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
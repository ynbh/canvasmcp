
import { tool } from "ai";
import { clearCourseNicknamesDataSchema } from "./aitm.schema.ts";
import { clearCourseNicknames, ClearCourseNicknamesData } from "..";

export default tool({
  description: `
  Clear course nicknames
Remove all stored course nicknames.
    `,
  parameters: clearCourseNicknamesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ClearCourseNicknamesData, "url"> ) => {
    try {
      const { data } = await clearCourseNicknames(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
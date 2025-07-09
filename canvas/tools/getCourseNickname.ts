
import { tool } from "ai";
import { getCourseNicknameDataSchema } from "./aitm.schema.ts";
import { getCourseNickname, GetCourseNicknameData } from "..";

export default tool({
  description: `
  Get course nickname
Returns the nickname for a specific course.
    `,
  parameters: getCourseNicknameDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCourseNicknameData, "url"> ) => {
    try {
      const { data } = await getCourseNickname(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
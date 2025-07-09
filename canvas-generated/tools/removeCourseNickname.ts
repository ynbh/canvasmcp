
import { tool } from "ai";
import { removeCourseNicknameDataSchema } from "./aitm.schema.ts";
import { removeCourseNickname, RemoveCourseNicknameData } from "..";

export default tool({
  description: `
  Remove course nickname
Remove the nickname for the given course.
Subsequent course API calls will
return the actual name for the course.
    `,
  parameters: removeCourseNicknameDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveCourseNicknameData, "url"> ) => {
    try {
      const { data } = await removeCourseNickname(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { setCourseNicknameDataSchema } from "./aitm.schema.ts";
import { setCourseNickname, SetCourseNicknameData } from "..";

export default tool({
  description: `
  Set course nickname
Set a nickname for the given course. This will replace the course's name
in
output of API calls you make subsequently, as well as in selected
places in the Canvas web user
interface.
    `,
  parameters: setCourseNicknameDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetCourseNicknameData, "url"> ) => {
    try {
      const { data } = await setCourseNickname(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
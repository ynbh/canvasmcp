
import { tool } from "ai";
import { listCourseNicknamesDataSchema } from "./aitm.schema.ts";
import { listCourseNicknames, ListCourseNicknamesData } from "..";

export default tool({
  description: `
  List course nicknames
Returns all course nicknames you have set.
    `,
  parameters: listCourseNicknamesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCourseNicknamesData, "url"> ) => {
    try {
      const { data } = await listCourseNicknames(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { listPagesCoursesDataSchema } from "./aitm.schema.ts";
import { listPagesCourses, ListPagesCoursesData } from "..";

export default tool({
  description: `
  List pages
A paginated list of the wiki pages associated with a course or group
    `,
  parameters: listPagesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPagesCoursesData, "url"> ) => {
    try {
      const { data } = await listPagesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
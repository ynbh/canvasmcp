
import { tool } from "ai";
import { listRevisionsCoursesDataSchema } from "./aitm.schema.ts";
import { listRevisionsCourses, ListRevisionsCoursesData } from "..";

export default tool({
  description: `
  List revisions
A paginated list of the revisions of a page. Callers must have update rights on the
page in order to see page history.
    `,
  parameters: listRevisionsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListRevisionsCoursesData, "url"> ) => {
    try {
      const { data } = await listRevisionsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
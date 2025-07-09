
import { tool } from "ai";
import { listContentExportsCoursesDataSchema } from "./aitm.schema.ts";
import { listContentExportsCourses, ListContentExportsCoursesData } from "..";

export default tool({
  description: `
  List content exports
A paginated list of the past and pending content export jobs for a
course,
group, or user. Exports are returned newest first.
    `,
  parameters: listContentExportsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListContentExportsCoursesData, "url"> ) => {
    try {
      const { data } = await listContentExportsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
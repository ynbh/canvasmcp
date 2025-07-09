
import { tool } from "ai";
import { listCoursesWithTheirLatestEpubExportDataSchema } from "./aitm.schema.ts";
import { listCoursesWithTheirLatestEpubExport, ListCoursesWithTheirLatestEpubExportData } from "..";

export default tool({
  description: `
  List courses with their latest ePub export
A paginated list of all courses a user is actively
participating in, and
the latest ePub export associated with the user & course.
    `,
  parameters: listCoursesWithTheirLatestEpubExportDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCoursesWithTheirLatestEpubExportData, "url"> ) => {
    try {
      const { data } = await listCoursesWithTheirLatestEpubExport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
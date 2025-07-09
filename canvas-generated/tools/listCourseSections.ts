
import { tool } from "ai";
import { listCourseSectionsDataSchema } from "./aitm.schema.ts";
import { listCourseSections, ListCourseSectionsData } from "..";

export default tool({
  description: `
  List course sections
A paginated list of the list of sections for this course.
    `,
  parameters: listCourseSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCourseSectionsData, "url"> ) => {
    try {
      const { data } = await listCourseSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
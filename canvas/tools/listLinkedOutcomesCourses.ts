
import { tool } from "ai";
import { listLinkedOutcomesCoursesDataSchema } from "./aitm.schema.ts";
import { listLinkedOutcomesCourses, ListLinkedOutcomesCoursesData } from "..";

export default tool({
  description: `
  List linked outcomes
A paginated list of the immediate OutcomeLink children of the outcome group.
    `,
  parameters: listLinkedOutcomesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLinkedOutcomesCoursesData, "url"> ) => {
    try {
      const { data } = await listLinkedOutcomesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { createNewGradingStandardCoursesDataSchema } from "./aitm.schema.ts";
import { createNewGradingStandardCourses, CreateNewGradingStandardCoursesData } from "..";

export default tool({
  description: `
  Create a new grading standard
Create a new grading standard

If grading_scheme_entry arguments are
omitted, then a default grading scheme
will be set. The default scheme is as follows:
"A" : 94,
"A-"
: 90,
"B+" : 87,
"B" : 84,
"B-" : 80,
"C+" : 77,
"C" : 74,
"C-" : 70,
"D+" : 67,
"D" : 64,
"D-" :
61,
"F" : 0,
    `,
  parameters: createNewGradingStandardCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateNewGradingStandardCoursesData, "url"> ) => {
    try {
      const { data } = await createNewGradingStandardCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { updateOutcomeGroupCoursesDataSchema } from "./aitm.schema.ts";
import { updateOutcomeGroupCourses, UpdateOutcomeGroupCoursesData } from "..";

export default tool({
  description: `
  Update an outcome group
Modify an existing outcome group. Fields not provided are left as
is;
unrecognized fields are ignored.

When changing the parent outcome group, the new parent group
must belong to
the same context as this outcome group, and must not be a descendant of
this outcome
group (i.e. no cycles allowed).
    `,
  parameters: updateOutcomeGroupCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateOutcomeGroupCoursesData, "url"> ) => {
    try {
      const { data } = await updateOutcomeGroupCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
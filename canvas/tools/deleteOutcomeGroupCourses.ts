
import { tool } from "ai";
import { deleteOutcomeGroupCoursesDataSchema } from "./aitm.schema.ts";
import { deleteOutcomeGroupCourses, DeleteOutcomeGroupCoursesData } from "..";

export default tool({
  description: `
  Delete an outcome group
Deleting an outcome group deletes descendant outcome groups and
outcome
links. The linked outcomes themselves are only deleted if all links to the
outcome were
deleted.

Aligned outcomes cannot be deleted; as such, if all remaining links to an
aligned outcome
are included in this group's descendants, the group
deletion will fail.
    `,
  parameters: deleteOutcomeGroupCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteOutcomeGroupCoursesData, "url"> ) => {
    try {
      const { data } = await deleteOutcomeGroupCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
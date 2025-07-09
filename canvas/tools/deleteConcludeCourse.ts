
import { tool } from "ai";
import { deleteConcludeCourseDataSchema } from "./aitm.schema.ts";
import { deleteConcludeCourse, DeleteConcludeCourseData } from "..";

export default tool({
  description: `
  Delete/Conclude a course
Delete or conclude an existing course
    `,
  parameters: deleteConcludeCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteConcludeCourseData, "url"> ) => {
    try {
      const { data } = await deleteConcludeCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
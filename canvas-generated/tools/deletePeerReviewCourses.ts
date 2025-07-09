
import { tool } from "ai";
import { deletePeerReviewCoursesDataSchema } from "./aitm.schema.ts";
import { deletePeerReviewCourses, DeletePeerReviewCoursesData } from "..";

export default tool({
  description: `
  Delete Peer Review
Delete a peer review for the assignment
    `,
  parameters: deletePeerReviewCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePeerReviewCoursesData, "url"> ) => {
    try {
      const { data } = await deletePeerReviewCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
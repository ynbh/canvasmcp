
import { tool } from "ai";
import { createPeerReviewCoursesDataSchema } from "./aitm.schema.ts";
import { createPeerReviewCourses, CreatePeerReviewCoursesData } from "..";

export default tool({
  description: `
  Create Peer Review
Create a peer review for the assignment
    `,
  parameters: createPeerReviewCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreatePeerReviewCoursesData, "url"> ) => {
    try {
      const { data } = await createPeerReviewCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { getAllPeerReviewsCoursesSubmissionsDataSchema } from "./aitm.schema.ts";
import { getAllPeerReviewsCoursesSubmissions, GetAllPeerReviewsCoursesSubmissionsData } from "..";

export default tool({
  description: `
  Get all Peer Reviews
Get a list of all Peer Reviews for this assignment
    `,
  parameters: getAllPeerReviewsCoursesSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllPeerReviewsCoursesSubmissionsData, "url"> ) => {
    try {
      const { data } = await getAllPeerReviewsCoursesSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
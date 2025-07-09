
import { tool } from "ai";
import { getAllPeerReviewsCoursesPeerReviewsDataSchema } from "./aitm.schema.ts";
import { getAllPeerReviewsCoursesPeerReviews, GetAllPeerReviewsCoursesPeerReviewsData } from "..";

export default tool({
  description: `
  Get all Peer Reviews
Get a list of all Peer Reviews for this assignment
    `,
  parameters: getAllPeerReviewsCoursesPeerReviewsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllPeerReviewsCoursesPeerReviewsData, "url"> ) => {
    try {
      const { data } = await getAllPeerReviewsCoursesPeerReviews(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
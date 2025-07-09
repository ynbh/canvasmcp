
import { tool } from "ai";
import { getAllPeerReviewsSectionsPeerReviewsDataSchema } from "./aitm.schema.ts";
import { getAllPeerReviewsSectionsPeerReviews, GetAllPeerReviewsSectionsPeerReviewsData } from "..";

export default tool({
  description: `
  Get all Peer Reviews
Get a list of all Peer Reviews for this assignment
    `,
  parameters: getAllPeerReviewsSectionsPeerReviewsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllPeerReviewsSectionsPeerReviewsData, "url"> ) => {
    try {
      const { data } = await getAllPeerReviewsSectionsPeerReviews(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
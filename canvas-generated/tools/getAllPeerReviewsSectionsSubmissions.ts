
import { tool } from "ai";
import { getAllPeerReviewsSectionsSubmissionsDataSchema } from "./aitm.schema.ts";
import { getAllPeerReviewsSectionsSubmissions, GetAllPeerReviewsSectionsSubmissionsData } from "..";

export default tool({
  description: `
  Get all Peer Reviews
Get a list of all Peer Reviews for this assignment
    `,
  parameters: getAllPeerReviewsSectionsSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllPeerReviewsSectionsSubmissionsData, "url"> ) => {
    try {
      const { data } = await getAllPeerReviewsSectionsSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
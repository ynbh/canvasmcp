
import { tool } from "ai";
import { deletePeerReviewSectionsDataSchema } from "./aitm.schema.ts";
import { deletePeerReviewSections, DeletePeerReviewSectionsData } from "..";

export default tool({
  description: `
  Delete Peer Review
Delete a peer review for the assignment
    `,
  parameters: deletePeerReviewSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePeerReviewSectionsData, "url"> ) => {
    try {
      const { data } = await deletePeerReviewSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { createPeerReviewSectionsDataSchema } from "./aitm.schema.ts";
import { createPeerReviewSections, CreatePeerReviewSectionsData } from "..";

export default tool({
  description: `
  Create Peer Review
Create a peer review for the assignment
    `,
  parameters: createPeerReviewSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreatePeerReviewSectionsData, "url"> ) => {
    try {
      const { data } = await createPeerReviewSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
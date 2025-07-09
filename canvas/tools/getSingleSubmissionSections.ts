
import { tool } from "ai";
import { getSingleSubmissionSectionsDataSchema } from "./aitm.schema.ts";
import { getSingleSubmissionSections, GetSingleSubmissionSectionsData } from "..";

export default tool({
  description: `
  Get a single submission
Get a single submission, based on user id.
    `,
  parameters: getSingleSubmissionSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleSubmissionSectionsData, "url"> ) => {
    try {
      const { data } = await getSingleSubmissionSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
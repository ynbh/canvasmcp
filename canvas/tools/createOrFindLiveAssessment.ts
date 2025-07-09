
import { tool } from "ai";
import { createOrFindLiveAssessmentDataSchema } from "./aitm.schema.ts";
import { createOrFindLiveAssessment, CreateOrFindLiveAssessmentData } from "..";

export default tool({
  description: `
  Create or find a live assessment
Creates or finds an existing live assessment with the given key and
aligns it with
the linked outcome
    `,
  parameters: createOrFindLiveAssessmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateOrFindLiveAssessmentData, "url"> ) => {
    try {
      const { data } = await createOrFindLiveAssessment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
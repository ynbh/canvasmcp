
import { tool } from "ai";
import { reActivateEnrollmentDataSchema } from "./aitm.schema.ts";
import { reActivateEnrollment, ReActivateEnrollmentData } from "..";

export default tool({
  description: `
  Re-activate an enrollment
Activates an inactive enrollment
    `,
  parameters: reActivateEnrollmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReActivateEnrollmentData, "url"> ) => {
    try {
      const { data } = await reActivateEnrollment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { concludeDeactivateOrDeleteEnrollmentDataSchema } from "./aitm.schema.ts";
import { concludeDeactivateOrDeleteEnrollment, ConcludeDeactivateOrDeleteEnrollmentData } from "..";

export default tool({
  description: `
  Conclude, deactivate, or delete an enrollment
Conclude, deactivate, or delete an enrollment. If the
+task+ argument isn't given, the enrollment
will be concluded.
    `,
  parameters: concludeDeactivateOrDeleteEnrollmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<ConcludeDeactivateOrDeleteEnrollmentData, "url"> ) => {
    try {
      const { data } = await concludeDeactivateOrDeleteEnrollment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
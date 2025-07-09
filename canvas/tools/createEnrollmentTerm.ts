
import { tool } from "ai";
import { createEnrollmentTermDataSchema } from "./aitm.schema.ts";
import { createEnrollmentTerm, CreateEnrollmentTermData } from "..";

export default tool({
  description: `
  Create enrollment term
Create a new enrollment term for the specified account.
    `,
  parameters: createEnrollmentTermDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateEnrollmentTermData, "url"> ) => {
    try {
      const { data } = await createEnrollmentTerm(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
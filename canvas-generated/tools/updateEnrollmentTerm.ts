
import { tool } from "ai";
import { updateEnrollmentTermDataSchema } from "./aitm.schema.ts";
import { updateEnrollmentTerm, UpdateEnrollmentTermData } from "..";

export default tool({
  description: `
  Update enrollment term
Update an existing enrollment term for the specified account.
    `,
  parameters: updateEnrollmentTermDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateEnrollmentTermData, "url"> ) => {
    try {
      const { data } = await updateEnrollmentTerm(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
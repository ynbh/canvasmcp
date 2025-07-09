
import { tool } from "ai";
import { deleteEnrollmentTermDataSchema } from "./aitm.schema.ts";
import { deleteEnrollmentTerm, DeleteEnrollmentTermData } from "..";

export default tool({
  description: `
  Delete enrollment term
Delete the specified enrollment term.
    `,
  parameters: deleteEnrollmentTermDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteEnrollmentTermData, "url"> ) => {
    try {
      const { data } = await deleteEnrollmentTerm(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
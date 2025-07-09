
import { tool } from "ai";
import { enrollmentByIdDataSchema } from "./aitm.schema.ts";
import { enrollmentById, EnrollmentByIdData } from "..";

export default tool({
  description: `
  Enrollment by ID
Get an Enrollment object by Enrollment ID
    `,
  parameters: enrollmentByIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<EnrollmentByIdData, "url"> ) => {
    try {
      const { data } = await enrollmentById(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
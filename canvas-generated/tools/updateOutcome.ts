
import { tool } from "ai";
import { updateOutcomeDataSchema } from "./aitm.schema.ts";
import { updateOutcome, UpdateOutcomeData } from "..";

export default tool({
  description: `
  Update an outcome
Modify an existing outcome. Fields not provided are left as is;
unrecognized
fields are ignored.

If any new ratings are provided, the combination of all new ratings
provided
completely replace any existing embedded rubric criterion; it is
not possible to tweak the ratings
of the embedded rubric criterion.

A new embedded rubric criterion's mastery_points default to the
maximum
points in the highest rating if not specified in the mastery_points
parameter. Any new
ratings lacking a description are given a default of "No
description". Any new ratings lacking a
point value are given a default of
0.
    `,
  parameters: updateOutcomeDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateOutcomeData, "url"> ) => {
    try {
      const { data } = await updateOutcome(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
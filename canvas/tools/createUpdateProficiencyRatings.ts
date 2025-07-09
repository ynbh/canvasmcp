
import { tool } from "ai";
import { createUpdateProficiencyRatingsDataSchema } from "./aitm.schema.ts";
import { createUpdateProficiencyRatings, CreateUpdateProficiencyRatingsData } from "..";

export default tool({
  description: `
  Create/update proficiency ratings
Create or update account-level proficiency ratings. These ratings
will apply to all
sub-accounts, unless they have their own account-level proficiency ratings
defined.
    `,
  parameters: createUpdateProficiencyRatingsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateUpdateProficiencyRatingsData, "url"> ) => {
    try {
      const { data } = await createUpdateProficiencyRatings(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
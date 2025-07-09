
import { tool } from "ai";
import { getProficiencyRatingsDataSchema } from "./aitm.schema.ts";
import { getProficiencyRatings, GetProficiencyRatingsData } from "..";

export default tool({
  description: `
  Get proficiency ratings
Get account-level proficiency ratings. If not defined for this account,
it
will return proficiency ratings for the nearest super-account with ratings defined.
Will return 404
if none found.

Examples:
curl https://<canvas>/api/v1/accounts/<account_id>/outcome_proficiency
\
-H 'Authorization: Bearer <token>'
    `,
  parameters: getProficiencyRatingsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetProficiencyRatingsData, "url"> ) => {
    try {
      const { data } = await getProficiencyRatings(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
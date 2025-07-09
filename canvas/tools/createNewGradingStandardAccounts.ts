
import { tool } from "ai";
import { createNewGradingStandardAccountsDataSchema } from "./aitm.schema.ts";
import { createNewGradingStandardAccounts, CreateNewGradingStandardAccountsData } from "..";

export default tool({
  description: `
  Create a new grading standard
Create a new grading standard

If grading_scheme_entry arguments are
omitted, then a default grading scheme
will be set. The default scheme is as follows:
"A" : 94,
"A-"
: 90,
"B+" : 87,
"B" : 84,
"B-" : 80,
"C+" : 77,
"C" : 74,
"C-" : 70,
"D+" : 67,
"D" : 64,
"D-" :
61,
"F" : 0,
    `,
  parameters: createNewGradingStandardAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateNewGradingStandardAccountsData, "url"> ) => {
    try {
      const { data } = await createNewGradingStandardAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
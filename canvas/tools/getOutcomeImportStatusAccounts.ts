
import { tool } from "ai";
import { getOutcomeImportStatusAccountsDataSchema } from "./aitm.schema.ts";
import { getOutcomeImportStatusAccounts, GetOutcomeImportStatusAccountsData } from "..";

export default tool({
  description: `
  Get Outcome import status
Get the status of an already created Outcome import. Pass 'latest' for the
outcome import id
for the latest import.

Examples:
curl
'https://<canvas>/api/v1/accounts/<account_id>/outcome_imports/<outcome_import_id>' \
-H
"Authorization: Bearer <token>"
curl
'https://<canvas>/api/v1/courses/<course_id>/outcome_imports/<outcome_import_id>' \
-H
"Authorization: Bearer <token>"
    `,
  parameters: getOutcomeImportStatusAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetOutcomeImportStatusAccountsData, "url"> ) => {
    try {
      const { data } = await getOutcomeImportStatusAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
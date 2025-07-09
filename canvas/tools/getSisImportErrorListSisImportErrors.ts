
import { tool } from "ai";
import { getSisImportErrorListSisImportErrorsDataSchema } from "./aitm.schema.ts";
import { getSisImportErrorListSisImportErrors, GetSisImportErrorListSisImportErrorsData } from "..";

export default tool({
  description: `
  Get SIS import error list
Returns the list of SIS import errors for an account or a SIS import.
Import
errors are only stored for 30 days.

Example:
curl
'https://<canvas>/api/v1/accounts/<account_id>/sis_imports/<id>/sis_import_errors' \
-H
"Authorization: Bearer <token>"

Example:
curl
'https://<canvas>/api/v1/accounts/<account_id>/sis_import_errors' \
-H "Authorization: Bearer
<token>"
    `,
  parameters: getSisImportErrorListSisImportErrorsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSisImportErrorListSisImportErrorsData, "url"> ) => {
    try {
      const { data } = await getSisImportErrorListSisImportErrors(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { getSisImportStatusDataSchema } from "./aitm.schema.ts";
import { getSisImportStatus, GetSisImportStatusData } from "..";

export default tool({
  description: `
  Get SIS import status
Get the status of an already created SIS import.

Examples:
curl
https://<canvas>/api/v1/accounts/<account_id>/sis_imports/<sis_import_id> \
-H 'Authorization:
Bearer <token>'
    `,
  parameters: getSisImportStatusDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSisImportStatusData, "url"> ) => {
    try {
      const { data } = await getSisImportStatus(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { getSisImportListDataSchema } from "./aitm.schema.ts";
import { getSisImportList, GetSisImportListData } from "..";

export default tool({
  description: `
  Get SIS import list
Returns the list of SIS imports for an account

Example:
curl
https://<canvas>/api/v1/accounts/<account_id>/sis_imports \
-H 'Authorization: Bearer <token>'
    `,
  parameters: getSisImportListDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSisImportListData, "url"> ) => {
    try {
      const { data } = await getSisImportList(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
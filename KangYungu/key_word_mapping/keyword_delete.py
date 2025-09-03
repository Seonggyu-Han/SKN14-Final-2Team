import os, argparse, json
from dotenv import load_dotenv
from pinecone import Pinecone

def main():
    load_dotenv()
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    ap = argparse.ArgumentParser("Delete vectors from Pinecone")
    ap.add_argument("--index", default="perfume-keywords")
    ap.add_argument("--namespace", default="keywords")
    ap.add_argument("--mode", choices=["all", "filter", "ids"], default="all")
    ap.add_argument("--type", default="keyword_label")
    ap.add_argument("--label_in", default="")
    ap.add_argument("--category_in", default="")
    ap.add_argument("--ids", nargs="*")
    args = ap.parse_args()

    index = pc.Index(args.index)

    if args.mode == "all":
        index.delete(delete_all=True, namespace=args.namespace)
        print(f"✔ Deleted ALL in ns='{args.namespace}' of index='{args.index}'")

    elif args.mode == "filter":
        flt = {"type": {"$eq": args.type}} if args.type else {}
        if args.label_in:
            labels = [s.strip() for s in args.label_in.split(",") if s.strip()]
            flt["label"] = {"$in": labels}
        if args.category_in:
            cats = [s.strip() for s in args.category_in.split(",") if s.strip()]
            flt["categories"] = {"$in": cats}
        index.delete(filter=flt, namespace=args.namespace)
        print(f"✔ Deleted with filter={json.dumps(flt, ensure_ascii=False)} in ns='{args.namespace}'")

    else:  # ids
        if not args.ids:
            raise SystemExit("ids 모드: --ids id1 id2 ...")
        index.delete(ids=args.ids, namespace=args.namespace)
        print(f"✔ Deleted {len(args.ids)} ids in ns='{args.namespace}'")

if __name__ == "__main__":
    main()

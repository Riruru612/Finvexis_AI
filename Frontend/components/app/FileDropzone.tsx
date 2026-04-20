import { useRef, useState } from "react";
import { UploadCloud, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FileDropzoneProps {
  fileName: string | null;
  disabled?: boolean;
  onFile: (file: File) => void;
  onClear: () => void;
}

const ACCEPTED = ".csv,.pdf,.xlsx,.xls,.json,.docx,.txt";

const FileDropzone = ({ fileName, disabled, onFile, onClear }: FileDropzoneProps) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);

  const handleFiles = (files: FileList | null) => {
    if (!files || !files.length) return;
    onFile(files[0]);
  };

  if (fileName) {
    return (
      <div className="flex items-center justify-between rounded-xl border border-border/60 bg-card/70 px-4 py-3.5">
        <div className="flex items-center gap-3 min-w-0">
          <div className="h-9 w-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center flex-shrink-0">
            <FileText className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <p className="text-sm text-foreground truncate">{fileName}</p>
            <p className="text-xs text-green-500 font-medium"> File is uploaded · ready for analysis</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClear}
          className="text-muted-foreground hover:text-destructive"
          aria-label="Remove file"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); if (!disabled) setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        if (disabled) return;
        handleFiles(e.dataTransfer.files);
      }}
      className={`relative rounded-xl border-2 border-dashed transition-colors p-8 text-center ${
        drag
          ? "border-primary bg-primary/5"
          : "border-border/70 bg-surface-muted/40 hover:border-primary/50 hover:bg-surface-muted/70"
      } ${disabled ? "opacity-60 pointer-events-none" : ""}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-3">
        <UploadCloud className="h-5 w-5" />
      </div>
      <p className="font-serif text-lg text-foreground">Upload your file to begin</p>
      <p className="text-xs text-muted-foreground mt-1.5">
        CSV · PDF · XLSX · JSON · DOCX — drag here or click to browse
      </p>
      <Button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="mt-5 bg-gradient-gold text-primary-foreground shadow-soft hover:opacity-95"
      >
        Choose file
      </Button>
    </div>
  );
};

export default FileDropzone;

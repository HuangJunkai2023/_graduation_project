param(
 [string]$SourcePptx=(Join-Path $PSScriptRoot 'inputs/OCS_Proposal_Defense_EN_v2.pptx'),
 [string]$TemplatePptx=(Join-Path $PSScriptRoot 'inputs/交大ppt模板-1.pptx'),
 [string]$Candidate=(Join-Path (Split-Path -Parent $PSScriptRoot) '.build/template-candidate.pptx')
)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$srcPath=[IO.Path]::GetFullPath($SourcePptx)
$tplPath=[IO.Path]::GetFullPath($TemplatePptx)
$destPath=[IO.Path]::GetFullPath($Candidate)
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destPath)|Out-Null
$white=0xFFFFFF
function SetText($s,[string]$value,[single]$size,[bool]$bold=$false){
 $s.TextFrame.TextRange.Text=$value
 $s.TextFrame.AutoSize=0
 $s.TextFrame.WordWrap=-1
 $s.TextFrame.MarginLeft=0;$s.TextFrame.MarginRight=0
 $s.TextFrame.MarginTop=0;$s.TextFrame.MarginBottom=0
 $r=$s.TextFrame.TextRange
 $r.Font.Name='Arial';$r.Font.Size=$size;$r.Font.Bold=[int]$bold*-1
 $r.Font.Color.RGB=$white
 $r.ParagraphFormat.Alignment=1
 $r.ParagraphFormat.Bullet.Visible=0
 $r.ParagraphFormat.SpaceBefore=0;$r.ParagraphFormat.SpaceAfter=0
 $r.ParagraphFormat.LineRuleWithin=-1;$r.ParagraphFormat.SpaceWithin=1
 $s.TextFrame.VerticalAnchor=1
 $s.TextFrame2.TextRange.Font.Fill.Solid()
 $s.TextFrame2.TextRange.Font.Fill.ForeColor.RGB=$white
 $s.TextFrame2.TextRange.Font.Fill.Transparency=0
}
$titles=@('','Standards consultation','An edition-specific query','Related work and research gap','Research aim and questions','System architecture','RQ1: Hybrid retrieval','RQ2 and RQ3: edition and evidence checks','Benchmark and controlled experiments','Evaluation metrics and planned targets','Preliminary progress and feasibility','Schedule and expected outcomes','','References','Hybrid scoring and selection','Evidence Gate and human scoring','Ablation definitions and denominators','Data risks and fallback scope')
$pp=$null;$source=$null;$dest=$null
$record=@()
try{
 $pp=New-Object -ComObject PowerPoint.Application
 $source=$pp.Presentations.Open($srcPath,-1,0,0)
 $dest=$pp.Presentations.Add(0)
 $dest.PageSetup.SlideWidth=960;$dest.PageSetup.SlideHeight=540
 for($i=1;$i -le 18;$i++){
   $ref=8
   if($i -eq 1){$ref=1}
   if($i -eq 13){$ref=9}
   $null=$dest.Slides.InsertFromFile($tplPath,$dest.Slides.Count,$ref,$ref)
   $s=$dest.Slides.Item($i)
   if($i -eq 1 -or $i -eq 13){
     $title=$s.Shapes.Item('标题 4')
     $title.Left=92;$title.Top=106;$title.Width=776;$title.Height=120
     if($i -eq 1){
       SetText $title "A Study on a Large-Model-Based Intelligent`nQuestion-Answering System for the`nOverhead Contact System Field" 30 $true
     }else{
       SetText $title 'Thank you' 52 $true
       $title.Top=117;$title.Height=80
     }
     $title.TextFrame.TextRange.ParagraphFormat.Alignment=2
     $title.Height=$(if($i -eq 1){120}else{80})
     $line=$s.Shapes.Item('直接连接符 174');$line.Top=231
     $p=$s.Shapes.Item('文本框 175');$p.Left=150;$p.Top=245;$p.Width=660;$p.Height=64
     if($i -eq 1){SetText $p "Junkai Huang  |  Student ID: 2023115799`nSupervisor: Prof. Deqing Huang" 18}
     else{SetText $p "Traceable answers to standards queries`nEdition checks and evidence-based refusal" 22}
     $p.TextFrame.TextRange.ParagraphFormat.Alignment=2
     $p.Height=64
     $d=$s.Shapes.Item('文本框 12');$d.Left=110;$d.Top=318;$d.Width=740;$d.Height=30
     if($i -eq 1){SetText $d 'SWJTU-Leeds Joint School  |  Undergraduate Project Proposal Defense' 17}
     else{SetText $d 'Questions and discussion' 22}
     $d.TextFrame.TextRange.ParagraphFormat.Alignment=2
     $d.Height=30
   }else{
     # Keep the actual template's title placeholder, shared header, school logo,
     # theme and layout. Remove only its unused body placeholder.
     for($j=$s.Shapes.Count;$j -ge 1;$j--){
       if($s.Shapes.Item($j).Name -ne '标题 1'){$s.Shapes.Item($j).Delete()}
     }
     $title=$s.Shapes.Item('标题 1')
     $size=30
     if($titles[$i-1].Length -gt 34){$size=27}
     SetText $title $titles[$i-1] $size $true
     $title.Left=65;$title.Top=10;$title.Width=720;$title.Height=38
     # Copy native content objects as a range: text, tables, images and connectors.
     # The v2 category and title occupy <100 pt and are replaced by the template.
     $indices=@()
     $original=$source.Slides.Item($i)
     for($j=1;$j -le $original.Shapes.Count;$j++){
       if($original.Shapes.Item($j).Top -ge 100){$indices+=$j}
     }
     if($indices.Count -gt 0){
       $original.Shapes.Range([object[]]$indices).Copy()
       $pasted=$s.Shapes.Paste()
       $record+=@{page=$i;templateSlide=$ref;copiedNativeObjects=$pasted.Count;title=$titles[$i-1]}
     }
   }
   $body=''
   foreach($n in $source.Slides.Item($i).NotesPage.Shapes){
     if($n.Type -eq 14 -and $n.PlaceholderFormat.Type -eq 2){$body=$n.TextFrame.TextRange.Text}
   }
   foreach($n in $s.NotesPage.Shapes){
     if($n.Type -eq 14 -and $n.PlaceholderFormat.Type -eq 2){
       $n.TextFrame.TextRange.Text=$body
       $n.TextFrame.TextRange.Font.Name='Microsoft YaHei'
       $n.TextFrame.TextRange.Font.Size=12
     }
   }
 }
 $dest.SaveAs($destPath,24)
 $record|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'validation/template-migration.json') -Encoding UTF8
 Write-Output $destPath
}finally{
 if($dest){$dest.Close();[Runtime.InteropServices.Marshal]::ReleaseComObject($dest)|Out-Null}
 if($source){$source.Close();[Runtime.InteropServices.Marshal]::ReleaseComObject($source)|Out-Null}
 if($pp){[Runtime.InteropServices.Marshal]::ReleaseComObject($pp)|Out-Null}
}
